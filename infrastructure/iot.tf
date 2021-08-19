resource "aws_iot_thing" "particle_sensor" {
  name = "particle_sensor"
}

resource "aws_iot_policy" "pubsub" {
  name = "PubSubToAnyTopic"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "iot:*",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iot_certificate" "cert" {
  active = true
}

resource "local_file" "certificate_pem" {
  content  = aws_iot_certificate.cert.certificate_pem
  filename = "../certs/certificate.pem"
}

resource "local_file" "private_key" {
  content  = aws_iot_certificate.cert.private_key
  filename = "../certs/private.key"
}

resource "local_file" "public_key" {
  content  = aws_iot_certificate.cert.public_key
  filename = "../certs/public.key"
}

resource "aws_iot_policy_attachment" "att" {
  policy = aws_iot_policy.pubsub.name
  target = aws_iot_certificate.cert.arn
}

resource "aws_iot_thing_principal_attachment" "att" {
  principal = aws_iot_certificate.cert.arn
  thing     = aws_iot_thing.particle_sensor.name
}

resource "aws_iam_role" "iot_topc_role" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "iot.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "sns_publish_policy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["sns:Publish"]
          Effect   = "Allow"
          Resource = "${aws_sns_topic.aqi_threshold_alarm.arn}"
        },
      ]
    })
  }
}

resource "aws_iot_topic_rule" "aqi_2_5_rule" {
  name        = "aqi_2_5_rule"
  enabled     = true
  sql         = "SELECT aqi AS aqi2_5 FROM 'air-quality.home-aqi-2-5' WHERE aqi > 50"
  sql_version = "2016-03-23"

  sns {
    message_format = "RAW"
    role_arn       = aws_iam_role.iot_topc_role.arn
    target_arn     = aws_sns_topic.aqi_threshold_alarm.arn
  }
}

resource "aws_iot_topic_rule" "aqi_10_rule" {
  name        = "aqi_10_rule"
  enabled     = true
  sql         = "SELECT aqi AS aqi10 FROM 'air-quality.home-aqi-10' WHERE aqi > 50"
  sql_version = "2016-03-23"

  sns {
    message_format = "RAW"
    role_arn       = aws_iam_role.iot_topc_role.arn
    target_arn     = aws_sns_topic.aqi_threshold_alarm.arn
  }
}
