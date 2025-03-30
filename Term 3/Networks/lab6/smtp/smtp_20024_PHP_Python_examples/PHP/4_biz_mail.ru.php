<?php

// Как активировать использование внешних приложений: https://proghunter.ru/articles/setting-up-the-smtp-mail-service-for-yandex-in-django?ysclid=ln7c5z1yvb904450406
// Кратко: id.yandex.ru -> Безопасность -> Доступы -> Пароли приложений -> Почта - > Новый пароль приложения -> Создать пароль и именно его ставим в $mail->Password

// пароль к учетке iu@iu.org.ru -> uOeYe_TTg1u2 

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
  $mail->Host = 'smtp.mail.ru';
  $mail->SMTPAuth   = true;
  $mail->Username   = 'iu@iu.org.ru';
  $mail->Password   = 'Nxd14F3dk4Cchi3v4ARZ'; // ВАЖНО! Это не пароль от ящике, это пароль для внешнего приложения, который добавляется из настроек ящика danila@bmstu.posevin.ru из свойств в правом верхнем углу, далее "пароль и безопасность", далее "безопасность", далее "пароль для внешних приложений".
  //$mail->Port = 465;
  $mail->Port = 587;
  $mail->setFrom("iu@iu.org.ru","Имя от кого отправлять");
  $mail->addAddress("danila@posevin.com","");//Кому отправляем
  $mail->addReplyTo("iu@iu.org.ru","Имя кому писать при ответе");
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

