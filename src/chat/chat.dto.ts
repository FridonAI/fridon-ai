import { BaseDto } from '@lib/common';

export class GetChatsResponseDto extends BaseDto<GetChatsResponseDto> {
  chats: {
    id: string;
  }[];
}

export class GetChatResponseDto extends BaseDto<GetChatResponseDto> {
  messages: {
    query: string;
    response?: string;
  }[];
}

export class CreateChatResponseDto extends BaseDto<CreateChatResponseDto> {
  chatId: string;
}

export class CreateChatMessageResponseDto extends BaseDto<CreateChatMessageResponseDto> {
  messageId: string;
}
