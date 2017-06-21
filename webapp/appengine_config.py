# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# https://stackoverflow.com/questions/41783864/importerror-no-module-named-ctypes-google-app-engine-with-bokeh-plot
import os, sys

on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
if on_appengine and os.name == 'nt':
    sys.platform = "Not Windows"
    
# [START vendor]
from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')
# [END vendor]
