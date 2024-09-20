import { BaseEvent } from '@lib/common';

export type AuxType = {
  walletId: string;
  chatId: string;
  personality: string;
  plugin?: string;
};

export class TransactionConfirmedEvent extends BaseEvent<TransactionConfirmedEvent> {
  public readonly transactionId: string;
  public readonly transactionType: string;
  public readonly aux: AuxType;
}

export class TransactionFailedEvent extends BaseEvent<TransactionFailedEvent> {
  public readonly transactionId: string;
  public readonly transactionType: string;
  public readonly aux: AuxType;
}

export class TransactionSkippedEvent extends BaseEvent<TransactionSkippedEvent> {
  public readonly transactionId: string;
  public readonly transactionType: string;
  public readonly aux: AuxType;
}

export class TransactionCanceledEvent extends BaseEvent<TransactionCanceledEvent> {
  public readonly reason: string;
  public readonly transactionType: string;
  public readonly aux: AuxType;
}
