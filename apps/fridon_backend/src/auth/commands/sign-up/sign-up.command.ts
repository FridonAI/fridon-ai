import type { ICommand } from '@nestjs/cqrs';

export class SignUpCommand implements ICommand {
  constructor(
    public readonly walletAddress: string,
    public readonly signature: string,
  ) {}
}
