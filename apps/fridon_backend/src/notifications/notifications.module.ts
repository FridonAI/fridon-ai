import { Module } from '@nestjs/common';
import { Redis } from 'ioredis';
import { NotificationsController } from './notifications.controller';
import { NotificationsRepository } from './notifications.repository';

@Module({
  controllers: [NotificationsController],
  providers: [
    NotificationsRepository,
    {
      provide: Redis,
      useValue: new Redis({
        host: process.env['REDIS_HOST'],
        port: parseInt(process.env['REDIS_PORT'] || '6379'),
      }),
    },
  ],
})
export class NotificationsModule {}
