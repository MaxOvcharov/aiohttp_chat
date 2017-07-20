/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

'use strict';

module.exports = {
  setMessage: setMessage
};
const uuidv4 = require('uuid/v4');
function setMessage(context, events, done) {
  // make it available to templates as "message"
  context.vars.user_id = uuidv4();
  context.vars.session_id = uuidv4();
  return done();
}
