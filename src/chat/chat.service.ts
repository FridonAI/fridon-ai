import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';
import { randomUUID } from 'crypto';
import { AiAdapter } from './external/ai/ai.adapter';
import { ChatRepository } from './chat.repository';

@Injectable()
export class ChatService {
  constructor(
    private readonly aiAdapter: AiAdapter,
    private readonly chatRepository: ChatRepository,
  ) {}

  async getChats(walletId: string): Promise<{ id: ChatId }[]> {
    const chats = await this.chatRepository.getChats(walletId);
    return chats.map((chat) => ({ id: new ChatId(chat.id) }));
  }

  async createChat(walletId: string): Promise<{ id: ChatId }> {
    const chatId = new ChatId(randomUUID());
    await this.chatRepository.createChat(chatId, walletId);
    return { id: chatId };
  }

  async getChat(chatId: ChatId) {
    const chat = await this.chatRepository.getChat(chatId);
    return {
      messages: chat.messages.map((message) => ({
        content: message.content,
        messageType: message.messageType,
      })),
    };
  }

  async createChatMessageQuery(
    chatId: ChatId,
    message: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);
    await this.chatRepository.createChatMessageQuery(
      chatId,
      chatMessageId,
      message,
    );
    this.aiAdapter.emitChatMessageCreated(chatId, chatMessageId, message);

    return { id: chatMessageId };
  }
}
