import { Module } from '@nestjs/common';
import { ChatController } from './chat.controller';
import { ChatService } from './chat.service';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { AiAdapter } from './external/ai/ai.adapter';

@Module({
  imports: [
    ClientsModule.register([
      { name: 'AI_SERVICE', transport: Transport.REDIS },
    ]),
  ],
  controllers: [ChatController],
  providers: [ChatService, AiAdapter],
})
export class ChatModule {}
