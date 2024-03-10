import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';

@Injectable()
export class ChatService {
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
    chatId: ChatId,
  ): Promise<{ messages: { query: string; response?: string }[] }> {
    chatId;
    return {
      messages: [
        { query: 'Hello World!', response: 'Hello!' },
        { query: 'How are you?', response: 'I am fine!' },
        { query: 'Hello?' },
      ],
    };
  }

  async createChatMessage(chatId: ChatId): Promise<{ id: ChatMessageId }> {
    chatId;
    return { id: new ChatMessageId('RANDOM_MESSAGE_ID_1') };
  }
}
