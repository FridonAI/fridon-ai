import { BadRequestException } from '@nestjs/common';
import { isUUID } from 'class-validator';

export class ChatMessageId {
  constructor(private readonly chatMessageId: string) {
    if (!chatMessageId) {
      throw new BadRequestException(
        `ChatId[${chatMessageId}] should not be empty`,
      );
    }

    if (!isUUID(chatMessageId)) {
      throw new BadRequestException(
        `ChatId[${chatMessageId}] should be a valid UUID`,
      );
    }
  }

  get value(): string {
    return this.chatMessageId;
  }
}
