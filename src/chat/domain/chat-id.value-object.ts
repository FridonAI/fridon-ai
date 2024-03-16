import { BadRequestException } from '@nestjs/common';
import { isUUID } from 'class-validator';

export class ChatId {
  constructor(readonly chatId: string) {
    if (!chatId) {
      throw new BadRequestException(`ChatId[${chatId}] should not be empty`);
    }

    if (!isUUID(chatId)) {
      throw new BadRequestException(`ChatId[${chatId}] should be a valid UUID`);
    }
  }

  get value(): string {
    return this.chatId;
  }
}
