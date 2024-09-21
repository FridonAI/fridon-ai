import {
  createParamDecorator,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { WalletSession } from '../types/types';

export const Wallet = createParamDecorator(
  (
    data: keyof WalletSession | undefined,
    ctx: ExecutionContext,
  ): WalletSession | string | number => {
    const request = ctx.switchToHttp().getRequest();

    const wallet = request.walletSession;
    if (!wallet) throw new UnauthorizedException();

    return data ? wallet?.[data] : wallet;
  },
);
