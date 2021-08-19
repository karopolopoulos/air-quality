resource "aws_sns_topic" "aqi_threshold_alarm" {
  display_name = "aqi_threshold_alarm_topic"
}

resource "aws_sns_topic_subscription" "sms_subscription" {
  topic_arn = aws_sns_topic.aqi_threshold_alarm.arn
  protocol  = "sms"
  endpoint  = var.notification_phone_number
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.aqi_threshold_alarm.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
