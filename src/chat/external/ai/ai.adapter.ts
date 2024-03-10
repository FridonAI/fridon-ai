import { Inject } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { ChatId } from 'src/chat/domain/chat-id.value-object';
import { ChatMessageId } from 'src/chat/domain/chat-message-id.value-object';
import { AiChatMessageCreatedDto } from './ai.dto';

export class AiAdapter {
  constructor(@Inject('AI_SERVICE') private client: ClientProxy) {}

  async emitChatMessageCreated(
    chatId: ChatId,
    chatMessageId: ChatMessageId,
    message: string,
  ) {
    this.client.emit(
      'chat_message_created',
      new AiChatMessageCreatedDto({
        chatId: chatId.value,
        chatMessageId: chatMessageId.value,
        message,
      }),
    );
  }
}
