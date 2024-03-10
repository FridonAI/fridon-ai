import { BaseDto } from '@lib/common';

export class AiChatMessageCreatedDto extends BaseDto<AiChatMessageCreatedDto> {
  chatId: string;
  chatMessageId: string;
  message: string;
}
