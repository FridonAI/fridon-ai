import { Module } from '@nestjs/common';
import { ChatHttpController } from './chat.controller';
import { ChatService } from './chat.service';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { AiAdapter } from './external/ai/ai.adapter';
import { ChatRepository } from './chat.repository';
import { AiEventsController } from './external/ai/ai.controller';
import {
  TransactionConfirmedHandler,
  TransactionSkippedHandler,
  TransactionFailedHandler,
  TransactionCanceledHandler,
} from './event-handlers/blockchain.evet-handlers';
import { Redis } from 'ioredis';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: 'AI_SERVICE',
        transport: Transport.REDIS,
        options: {
          host: process.env['REDIS_HOST'],
          port: parseInt(process.env['REDIS_PORT'] || '6379'),
        },
      },
    ]),
  ],
  controllers: [ChatHttpController, AiEventsController],
  providers: [
    ChatService,
    ChatRepository,
    AiAdapter,
    TransactionConfirmedHandler,
    TransactionSkippedHandler,
    TransactionFailedHandler,
    TransactionCanceledHandler,
    {
      provide: Redis,
      useValue: new Redis({
        host: process.env['REDIS_HOST'],
        port: parseInt(process.env['REDIS_PORT'] || '6379'),
      }),
    },
  ],
})
export class ChatModule {}
