import { Module } from '@nestjs/common';
import { ChatController } from './chat.controller';
import { ChatService } from './chat.service';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { AiAdapter } from './external/ai/ai.adapter';
import { ChatRepository } from './chat.repository';

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
  controllers: [ChatController],
  providers: [ChatService, ChatRepository, AiAdapter],
})
export class ChatModule {}
