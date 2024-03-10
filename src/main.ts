import { NestFactory } from '@nestjs/core';
import { AppModule } from './main.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('Chat Block AI [API]')
    .setDescription('The Chat Block AI API description')
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.REDIS,
  });

  await app.startAllMicroservices();
  await app.listen(3000);
}
bootstrap();
