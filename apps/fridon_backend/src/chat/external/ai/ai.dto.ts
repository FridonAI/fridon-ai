import { BaseDto } from '@lib/common';

export class AiChatMessageCreatedDto extends BaseDto<AiChatMessageCreatedDto> {
  chatId: string;
  user: {
    walletId: string;
  };
  plugins: string[];
  data: {
    message: string;
    personality: string;
    messageId: string;
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
  chat_id: string;
  user: {
    wallet_id: string;
  };
  data: {
    id?: string;
    message?: string;
    serialized_transaction?: number[];
    structured_messages?: string[];
    messageId?: string;
    pluginsUsed?: string[];
  };
  aux: AiAuxiliaryMessage;
}

export type AiAuxiliaryMessage = {
  traceId: string;
};

// Score Updated
export class AiScoreUpdatedDto {
  walletId: string;
  score: number;
  pluginsUsed: string[];
  chatId: string;
}
