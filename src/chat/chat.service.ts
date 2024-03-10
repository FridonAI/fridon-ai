import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';
import { randomUUID } from 'crypto';
import { AiAdapter } from './external/ai/ai.adapter';

@Injectable()
export class ChatService {
  constructor(private readonly aiAdapter: AiAdapter) {}

  async getChats(): Promise<{ id: ChatId }[]> {
    return [
      { id: new ChatId('RANDOM_ID_1') },
      { id: new ChatId('RANDOM_ID_2') },
      { id: new ChatId('RANDOM_ID_3') },
    ];
  }

  async createChat(): Promise<{ id: ChatId }> {
    return { id: new ChatId('RANDOM_ID_3') };
  }

  async getChat(
    _: ChatId,
  ): Promise<{ messages: { query: string; response?: string }[] }> {
    return {
      messages: [
        { query: 'Hello World!', response: 'Hello!' },
        { query: 'How are you?', response: 'I am fine!' },
        { query: 'Hello?' },
      ],
    };
  }

  async createChatMessage(chatId: ChatId): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    this.aiAdapter.emitChatMessageCreated(chatId, chatMessageId, 'Hello!');
    return { id: chatMessageId };
  }
}
