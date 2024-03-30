import { BaseEvent } from '@lib/common';

export type AuxType = {
  chatId: string;
  narrator: string;
};

export class TransactionConfirmedEvent extends BaseEvent<TransactionConfirmedEvent> {
  public readonly transactionId: string;
  public readonly aux: AuxType;
}

export class TransactionFailedEvent extends BaseEvent<TransactionFailedEvent> {
  public readonly transactionId: string;
  public readonly aux: AuxType;
}

export class TransactionSkippedEvent extends BaseEvent<TransactionSkippedEvent> {
  public readonly transactionId: string;
  public readonly aux: AuxType;
}

export class TransactionCouldnotSendEvent extends BaseEvent<TransactionCouldnotSendEvent> {
  public readonly message: string;
  public readonly aux: AuxType;
}
