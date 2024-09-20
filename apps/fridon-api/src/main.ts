import { NestFactory } from '@nestjs/core';
import { AppModule } from './main.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { ValidationPipe } from '@nestjs/common';
import morgan from 'morgan';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('Chat Block AI [API]')
    .setDescription('The Chat Block AI API description')
    .setVersion('1.0')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.REDIS,
    options: {
      host: process.env['REDIS_HOST'],
      port: parseInt(process.env['REDIS_PORT'] || '6379'),
    },
  });

  app.use(morgan('tiny'));
  app.useGlobalPipes(
    new ValidationPipe({
      transform: true,
    }),
  );
  app.enableCors();

  await app.startAllMicroservices();
  await app.listen(3000);
}
bootstrap();
