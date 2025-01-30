import { HttpException, HttpStatus, Logger } from '@nestjs/common';
import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { AuthRepository } from '../../database/auth.repository';
import { verify } from '../../domain/utils';
import { SignUpCommand } from './sign-up.command';

/**
 * This service ...
 */
@CommandHandler(SignUpCommand)
export class SignUpService implements ICommandHandler<SignUpCommand> {
  private readonly logger = new Logger(SignUpService.name);

  constructor(private authRepository: AuthRepository) {}

  async execute(command: SignUpCommand) {
    this.logger.debug('CreateUserService executed!');

    const { walletAddress, signature } = command;

    console.log(walletAddress, signature);

    // 1. Check Nonce
    const nonce = await this.authRepository.getNonce(walletAddress);
    if (!nonce) {
      throw new HttpException('WalletNotFound', HttpStatus.NOT_FOUND);
    }

    if (nonce.verifiedAt) {
      throw new HttpException('Wallet Already Registered', 409);
    }

    // 2. Verify
    if (
      !(
        verify(nonce.nonce, signature, walletAddress, 'raw') ||
        verify(nonce.nonce, signature, walletAddress, 'transaction') ||
        verify(nonce.nonce, signature, walletAddress, 'versionedTransaction')
      )
    ) {
      throw new HttpException('SignatureInvalid', HttpStatus.FORBIDDEN);
    }

    await this.authRepository.verifyWallet(walletAddress);
  }
}
