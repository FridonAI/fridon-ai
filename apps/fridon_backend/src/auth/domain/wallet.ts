import { NonFunctionProperties } from '@lib/common';

export type WalletConstructor = Pick<
  NonFunctionProperties<Omit<Wallet, 'props'>>,
  | 'walletAddress'
  | 'userType'
  | 'nonce'
  | 'expirationTime'
  | 'verifiedAt'
  | 'createdAt'
  | 'updatedAt'
>;

export class Wallet {
  readonly walletAddress: string;
  readonly nonce: string;

  readonly userType?: string | undefined;
  readonly expirationTime?: number | undefined;
  readonly verifiedAt?: string | undefined;

  readonly createdAt: Date;
  readonly updatedAt: Date;

  constructor(props: WalletConstructor) {
    Object.assign(this, props);
  }

  validate() {
    // todo: implement
  }
}
