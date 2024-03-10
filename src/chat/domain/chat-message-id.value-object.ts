export class ChatMessageId {
  constructor(readonly chatMessageId: string) {}

  get value(): string {
    return this.chatMessageId;
  }
}
