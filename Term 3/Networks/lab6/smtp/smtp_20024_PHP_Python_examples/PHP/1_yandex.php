#/usr/bin/php
<?php

// Как активировать использование внешних приложений: https://proghunter.ru/articles/setting-up-the-smtp-mail-service-for-yandex-in-django?ysclid=ln7c5z1yvb904450406
// Кратко: id.yandex.ru -> Безопасность -> Доступы -> Пароли приложений -> Почта - > Новый пароль приложения -> Создать пароль и именно его ставим в $mail->Password

// Подключаем библиотеку PHPMailer
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';
require 'PHPMailer/src/Exception.php';
 
$mail = new PHPMailer(true);

try {
  $mail->SMTPDebug = SMTP::DEBUG_SERVER;
  $mail->isSMTP();
  $mail->Host = 'smtp.yandex.ru';
  $mail->SMTPAuth   = true;
  $mail->Username   = 'robotland2@yandex.ru';
  $mail->Password   = 'fcogbelywgwutrbh';
  //$mail->Port = 465;
  $mail->Port = 587;
  $mail->setFrom("robotland2@yandex.ru","Имя от кого отправлять");
  $mail->addAddress("danila@posevin.com","");//Кому отправляем
  //$mail->addReplyTo("robotland2@yandex.ru","Имя кому писать при ответе");
  $mail->SMTPSecure = 'tls';
  $mail->isHTML(true);//HTML формат
  $mail->Subject = "Тема сообщения";
  $mail->Body    = "Содержание сообщения";
  $mail->AltBody = "Альтернативное содержание сообщения";

  $mail->send();
  echo "Сообщение отправлено";
} catch (Exception $e) {
  echo "Ошибка отправки: {$mail->ErrorInfo}";
}
?>
