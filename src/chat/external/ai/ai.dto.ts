import { BaseDto } from '@lib/common';

export class AiChatMessageCreatedDto extends BaseDto<AiChatMessageCreatedDto> {
  chatId: string;
  user: {
    walletId: string;
  };
  data: {
    message: string;
  };
  aux: AiAuxiliaryMessage;
}

export class AiChatMessageInfoCreatedDto extends BaseDto<AiChatMessageInfoCreatedDto> {
  chatId: string;
  user: {
    walletId: string;
  };
  data: {
    message: string;
  };
  aux: AiAuxiliaryMessage;
}

export class AiChatMessageResponseGeneratedDto extends BaseDto<AiChatMessageResponseGeneratedDto> {
  chatId: string;
  user: {
    walletId: string;
  };
  data: {
    message: string;
  };
  aux: AiAuxiliaryMessage;
}

export type AiAuxiliaryMessage = {
  traceId: string;
};
