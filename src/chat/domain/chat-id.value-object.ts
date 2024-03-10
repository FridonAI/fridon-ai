export class ChatId {
  constructor(readonly chatId: string) {}

  get value(): string {
    return this.chatId;
  }
}
