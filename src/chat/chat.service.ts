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

  async getChats(walletId: string): Promise<{ id: ChatId; title?: string }[]> {
    const chats = await this.chatRepository.getChats(walletId);
    return chats.map((chat) => ({
      id: new ChatId(chat.id),
      title: chat.messages[0]?.content,
    }));
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
    walletId: string,
    message: string,
    narrator: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'Query',
      chatId: chatId.value,
      content: message,
      narrator,
    });

    this.aiAdapter.emitChatMessageCreated(chatId, walletId, message, narrator);

    return { id: chatMessageId };
  }

  async createChatMessageTransactionResponse(
    chatId: ChatId,
    data: string,
    narrator: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'TransactionResponse',
      chatId: chatId.value,
      content: data,
      narrator: narrator,
    });
    this.aiAdapter.emitChatMessageInfoCreated(chatId, data);

    return { id: chatMessageId };
  }

  async createChatMessageAiResponse(
    chatId: ChatId,
    data: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'Response',
      chatId: chatId.value,
      content: data,
    });
    this.aiAdapter.emitChatMessageInfoCreated(chatId, data);

    return { id: chatMessageId };
  }
}
