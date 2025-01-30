import type { ICommand } from '@nestjs/cqrs';

export class SignInCommand implements ICommand {
  constructor(
    public readonly walletAddress: string,
    public readonly signature: string,
  ) {}
}
