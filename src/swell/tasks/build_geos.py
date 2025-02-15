# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class BuildGeos(taskBase):

    def execute(self):

        self.logger.info('BuildGeos')


# --------------------------------------------------------------------------------------------------
