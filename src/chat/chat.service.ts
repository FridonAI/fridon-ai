import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';
import { randomUUID } from 'crypto';
import { AiAdapter } from './external/ai/ai.adapter';
import { ChatRepository } from './chat.repository';
import { UserService } from 'src/user/user.service';

enum MessageType {
  Query = 'Query',
  Response = 'Response',
  TransactionResponse = 'TransactionResponse',
}

type ChatMessage = {
  id: string;
  content: string;
  messageType: MessageType;
  personality: string | null;
  plugins: string[];
  createdAt: Date;
  updatedAt: Date;
};

type Chat = {
  id: string;
  walletId: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
};

@Injectable()
export class ChatService {
  constructor(
    private readonly aiAdapter: AiAdapter,
    private readonly chatRepository: ChatRepository,
    private readonly userService: UserService,
  ) {}

  async getChats(walletId: string): Promise<{ id: ChatId; title?: string }[]> {
    const chats = await this.chatRepository.getChats(walletId);
    return chats.map((chat) => ({
      id: new ChatId(chat.id),
      title: chat.messages[0]?.content,
    }));
  }

  async getChatNotifications(walletId: string) {
    const notificationChat =
      await this.chatRepository.getChatNotifications(walletId);

    return {
      messages: notificationChat
        ? notificationChat?.messages.map((message) => ({
            id: message.id,
            content: message.content,
            messageType: message.messageType,
            date: message.createdAt,
          }))
        : [],
    };
  }

  async getChatHistory(walletId: string, limit: number) {
    const messages = await this.chatRepository.getChatHistory(walletId, limit);

    const chatMap = new Map<string, Chat>();

    messages.forEach((message) => {
      const chatId = message.chatId;
      if (!chatMap.has(chatId)) {
        chatMap.set(chatId, {
          id: message.Chat.id,
          walletId: message.Chat.walletId,
          messages: [],
          createdAt: message.Chat.createdAt,
          updatedAt: message.Chat.updatedAt,
        });
      }

      chatMap.get(chatId)?.messages.push({
        id: message.id,
        content: message.content,
        messageType: message.messageType as MessageType,
        personality: message.personality,
        plugins: message.plugins,
        createdAt: message.createdAt,
        updatedAt: message.updatedAt,
      });
    });

    const chats = Array.from(chatMap.values());

    return chats.map((chat) => ({
      id: new ChatId(chat.id),
      walletId: chat.walletId,
      messages: chat.messages.map((message) => ({
        id: message.id,
        content: message.content,
        messageType: message.messageType,
        personality: message.personality,
        plugins: message.plugins,
        createdAt: message.createdAt,
        updatedAt: message.updatedAt,
      })),
      createdAt: chat.createdAt,
      updatedAt: chat.updatedAt,
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
        id: message.id,
        content: message.content,
        messageType: message.messageType,
      })),
    };
  }

  async createChatMessageQuery(
    chatId: ChatId,
    walletId: string,
    message: string,
    personality: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'Query',
      chatId: chatId.value,
      content: message,
      personality,
    });
    const userPlugins = await this.userService.getUserPlugins(walletId);

    this.aiAdapter.emitChatMessageCreated(
      chatId,
      chatMessageId.value,
      walletId,
      message,
      personality,
      userPlugins.map((plugin) => plugin.id),
    );

    return { id: chatMessageId };
  }

  async createChatMessageTransactionResponse(
    chatId: ChatId,
    data: string,
    personality: string,
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'TransactionResponse',
      chatId: chatId.value,
      content: data,
      personality: personality,
    });
    await this.aiAdapter.emitChatMessageInfoCreated(chatId, data);

    return { id: chatMessageId };
  }

  async createChatMessageAiResponse(
    chatId: ChatId,
    messageId: ChatMessageId | undefined,
    data: string,
    plugins: string[],
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'Response',
      chatId: chatId.value,
      content: data,
      plugins,
    });

    if (messageId) {
      await this.chatRepository.updateChatMessage(messageId.value, plugins);
    }

    return { id: chatMessageId };
  }
}
