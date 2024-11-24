LOG_CLOCK = "clock"
LOG_TIME_STAMP = "timestamp"
LOG_EMOTION = "emotion"
LOG_ACTION = "action"
LOG_HEAD_ANGLE = "head_angle"
LOG_ECHO_DISTANCE = "echo_distance"
LOG_FLOOR = "floor"
LOG_YAW = "yaw"
LOG_DURATION1 = "duration1"
LOG_CELL = "cell"
LOG_POSITION_PE = "position_pe"
LOG_OUTCOME = "outcome"
LOG_PREDICTED_OUTCOME = "predicted_outcome"
LOG_RE_YAW = "re_yaw"
LOG_RE_COMPASS = "re_compass"
LOG_AZIMUTH = "azimuth"
LOG_SPEED = "speed"
LOG_FORWARD_PE = "forward_pe"

# TRACE_HEADERS = [LOG_CLOCK, LOG_TIME_STAMP, LOG_EMOTION, LOG_ACTION, LOG_PREDICTED_OUTCOME, LOG_OUTCOME,
# LOG_HEAD_ANGLE, LOG_ECHO_DISTANCE, LOG_FLOOR,
#                  LOG_YAW, LOG_DURATION1, LOG_CELL, LOG_POSITION_PE, LOG_RE_YAW, LOG_RE_COMPASS]
TRACE_HEADERS = [LOG_CLOCK, LOG_TIME_STAMP, LOG_ACTION, LOG_HEAD_ANGLE, LOG_ECHO_DISTANCE, LOG_YAW, LOG_DURATION1,
                 LOG_AZIMUTH, LOG_RE_COMPASS, LOG_OUTCOME, LOG_CELL, LOG_POSITION_PE, LOG_SPEED, LOG_FORWARD_PE]
TRACE_FILE = 'log/00_trace.csv'