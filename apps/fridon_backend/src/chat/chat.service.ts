import { HttpException, Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';
import { randomUUID } from 'crypto';
import { AiAdapter } from './external/ai/ai.adapter';
import { ChatRepository } from './chat.repository';
import { UserService } from 'src/user/user.service';
import { RectangleId } from './domain/rectangle-id.value-object';

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
  structuredData: string | null;
  plugins: string[];
  createdAt: Date;
  updatedAt: Date;
};

type Rectangle = {
  id: string;
  coin: string;
  startDate: Date;
  endDate: Date;
  startPrice: number;
  endPrice: number;
  interval: string;
};

type Chat = {
  id: string;
  walletId: string;
  chatType: 'Regular' | 'SuperChart';
  messages: ChatMessage[];
  rectangle: Rectangle | null;
  model: string;
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

  async getChats(
    walletId: string,
    chatType: 'Regular' | 'SuperChart',
  ): Promise<
    {
      id: ChatId;
      title?: string;
      rectangle?: Rectangle;
      model: string;
    }[]
  > {
    const chats = await this.chatRepository.getChats(walletId, chatType);
    return chats.map((chat) => ({
      id: new ChatId(chat.id),
      title: chat.messages[0]?.content,
      rectangle: chat.rectangle
        ? {
            id: chat.rectangle.id,
            coin: chat.rectangle.symbol,
            startDate: chat.rectangle.startDate,
            endDate: chat.rectangle.endDate,
            startPrice: chat.rectangle.startPrice,
            endPrice: chat.rectangle.endPrice,
            interval: chat.rectangle.interval,
          }
        : undefined,
      model: chat.model,
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
            structuredData: message.structuredData,
            date: message.createdAt,
          }))
        : [],
    };
  }

  async getBonkNotifications(walletId: string) {
    const notificationChat =
      await this.chatRepository.getBonkNotifications(walletId);

    return {
      messages: notificationChat
        ? notificationChat?.messages.map((message) => ({
            id: message.id,
            content: message.content,
            messageType: message.messageType,
            structuredData: message.structuredData,
            date: message.createdAt,
          }))
        : [],
    };
  }

  async getChatHistory(
    walletId: string,
    limit: number,
    chatType: 'Regular' | 'SuperChart',
  ) {
    const messages = await this.chatRepository.getChatHistory(walletId, limit);

    const chatMap = new Map<string, Chat>();

    messages.forEach((message) => {
      if (message.Chat.chatType !== chatType) {
        return;
      }
      const chatId = message.chatId;
      if (!chatMap.has(chatId)) {
        chatMap.set(chatId, {
          id: message.Chat.id,
          walletId: message.Chat.walletId,
          chatType: message.Chat.chatType,
          rectangle: message.Chat.rectangle,
          messages: [],
          createdAt: message.Chat.createdAt,
          updatedAt: message.Chat.updatedAt,
          model: message.Chat.model,
        });
      }

      chatMap.get(chatId)?.messages.push({
        id: message.id,
        content: message.content,
        messageType: message.messageType as MessageType,
        structuredData: message.structuredData,
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
      chatType: chat.chatType,
      rectangle: chat.rectangle
        ? {
            id: chat.rectangle.id,
            coin: chat.rectangle.symbol,
            startDate: chat.rectangle.startDate,
            endDate: chat.rectangle.endDate,
            startPrice: chat.rectangle.startPrice,
            endPrice: chat.rectangle.endPrice,
            interval: chat.rectangle.interval,
          }
        : undefined,
      messages: chat.messages.map((message) => ({
        id: message.id,
        content: message.content,
        messageType: message.messageType,
        personality: message.personality,
        structuredData: message.structuredData,
        plugins: message.plugins,
        createdAt: message.createdAt,
        updatedAt: message.updatedAt,
      })),
      createdAt: chat.createdAt,
      updatedAt: chat.updatedAt,
      model: chat.model,
    }));
  }

  async createChat(
    walletId: string,
    options?: {
      rectangle?: Rectangle;
      model?: string;
    },
  ): Promise<{ id: ChatId }> {
    const userData = await this.userService.getWalletVerification(walletId);
    console.log(userData);
    if (!userData || !userData?.verified) {
      throw new HttpException(
        'User not verified! Please verify your wallet address By Transferring.',
        400,
      );
    }

    const chatId = new ChatId(randomUUID());

    if (options?.rectangle) {
      const rectangleId = new RectangleId(randomUUID());
      options.rectangle.id = rectangleId.value;
    }

    await this.chatRepository.createChat(
      chatId,
      walletId,
      options?.rectangle,
      options?.model ?? 'gpt-4o',
    );

    return { id: chatId };
  }

  async getChat(chatId: ChatId) {
    const chat = await this.chatRepository.getChat(chatId);
    return {
      messages: chat.messages.map((message) => ({
        id: message.id,
        content: message.content,
        structuredData: message.structuredData,
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
    const chat = await this.chatRepository.getChat(chatId);

    let finalMessage = message;
    if (chat.rectangle) {
      finalMessage = `${message} for ${chat.rectangle.symbol} from ${chat.rectangle.startDate.toISOString()} to ${chat.rectangle.endDate.toISOString()} with ${chat.rectangle.interval} timeframe`;
    }

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
      finalMessage,
      personality,
      userPlugins.map((plugin) => plugin.id),
      chat.model,
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
    data: { message?: string; structured_messages?: any },
    plugins: string[],
  ): Promise<{ id: ChatMessageId }> {
    const chatMessageId = new ChatMessageId(randomUUID());
    await this.getChat(chatId);

    await this.chatRepository.createChatMessage({
      id: chatMessageId.value,
      messageType: 'Response',
      chatId: chatId.value,
      content: data.message ?? '',
      structuredData: data.structured_messages
        ? JSON.stringify(data.structured_messages)
        : null,
      plugins,
    });

    if (messageId) {
      await this.chatRepository.updateChatMessage(messageId.value, plugins);
    }

    return { id: chatMessageId };
  }
}
