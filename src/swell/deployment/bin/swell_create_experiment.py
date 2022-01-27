#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
import os
import shutil
import yaml

from swell.utilities.logger import Logger
from swell.utilities.git_utils import git_got
import swell.deployment.yaml_exploder as ye
import swell.deployment.prep_exp_dirs as ped
import swell.deployment.prep_suite as ps


# --------------------------------------------------------------------------------------------------


@click.command()
@click.argument('config')
@click.option('--clean', '-c', is_flag=True, help='Remove any existing experiment directory')
def main(config, clean):

  # Load experiment file
  # --------------------
  with open(config, 'r') as ymlfile:
    config_dict = yaml.safe_load(ymlfile)

  # Create a logger
  # ---------------
  logger = Logger('swell_create_experiment')

  # Create experiment directory
  # ---------------------------
  user = os.environ['USER']   # Allow for ${USER} in root path
  exp_root = config_dict['experiment_root'].replace('${USER}', user)

  exp_id = config_dict['experiment_id']
  exp_id_dir = os.path.join(exp_root, exp_id)

  logger.info('Creating experiment directory: '+exp_id_dir)

  # Platform
  # --------
  platform = config_dict['platform_name']

  # Optionally clean up any existing directory
  # ------------------------------------------
  if clean:
    check_clean = input('swell_create_experiment: removing existing experiment directory '+
                        exp_id_dir+'. Press return to continue')
    logger.info('removing'+exp_id_dir)
    shutil.rmtree(exp_id_dir)

  # Create the experiment directory
  # -------------------------------
  try:
    os.makedirs(exp_id_dir)
  except Exception:
    logger.info('Experiment directory is already present')

  # Copy experiment.yaml to the experiment directory with the experiment id name
  shutil.copy(config, os.path.join(exp_id_dir, 'experiment_{}.yaml'.format(exp_id)))
  logger.info('Experiment yaml copied to working directory...')

  # Set the suite and add environmental variables to the experiment yaml
  # --------------------------------------------------------------------
  suite = ped.dir_config(logger, config_dict['suite']['suite name'], platform, exp_id_dir, exp_id,
                         ('suite_dir', exp_id+'-suite'), ('bundle', 'bundle'),
                         ('stage_dir', 'stage'), ('experiment_dir', 'run'),
                         ('jedi_build', 'bundle/build'))

  # Clone the git repos needed for the yaml file explosion
  # ------------------------------------------------------
  needed_repos = ['oops'] # Always clone oops
  # Read input file as text file and find lines
  match_string = 'yaml::'
  config_file = open(config, 'r')
  for line in config_file:
    if match_string in line:
      # Extract repo name
      needed_repos.append(line.partition(match_string)[2].split('/')[1])
  # Remove duplicates
  needed_repos = list(set(needed_repos))

  # Clone only the needed repos
  repo_dict = config_dict['build jedi']['bundle repos']
  for d in repo_dict:
    if d['project'] in needed_repos:
      project = d['project']
      git_url = d['git url']
      branch  = d['branch']
      proj_dir = os.path.join(suite.dir_dict['bundle'], project)
      logger.info('cloning branch {} of {}'.format(branch, git_url))
      git_got(git_url, branch, proj_dir)

  # Expand yaml and add cfg yaml variables at the root level
  # --------------------------------------------------------
  big_yaml = ye.yaml_exploder(exp_id_dir, suite.dir_dict['suite_dir'], suite.dir_dict)
  big_yaml.boom()

  # Prepare the suite driver file
  # -----------------------------
  suite_prep = ps.PrepSuite(logger, platform, big_yaml.target)

  # Write the complete experiment yaml to suite directory
  # -----------------------------------------------------
  big_yaml.write()

# --------------------------------------------------------------------------------------------------

if __name__ == "__main__":
  main()

# --------------------------------------------------------------------------------------------------
