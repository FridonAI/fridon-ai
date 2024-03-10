import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';

export class GetChatsResponseDto extends BaseDto<GetChatsResponseDto> {
  @ApiProperty({ example: [{ id: 'chatId' }] })
  chats: {
    id: string;
  }[];
}

export class GetChatResponseDto extends BaseDto<GetChatResponseDto> {
  @ApiProperty({
    example: [
      { query: 'hello', response: 'hi' },
      { query: 'hello 2', response: 'hi 2' },
    ],
  })
  messages: {
    query: string;
    response?: string;
  }[];
}

export class CreateChatResponseDto extends BaseDto<CreateChatResponseDto> {
  @ApiProperty({ example: 'chatId' })
  chatId: string;
}

export class CreateChatMessageResponseDto extends BaseDto<CreateChatMessageResponseDto> {
  @ApiProperty({ example: 'messageId' })
  messageId: string;
}
