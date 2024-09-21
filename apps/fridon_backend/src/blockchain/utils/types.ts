export type Response<T> =
  | {
      completed: true;
      data: T;
    }
  | {
      completed: false;
      error: string;
      data?: {
        metadata?: string;
      };
    };

export type TokenListJsonType = {
  address: string;
  chainId: number;
  decimals: number;
  name: string;
  symbol: string;
  logoURI: string;
  tags: string[];
  extensions: any;
};

export type TokenListType = SplTokenType[];

export type SplTokenType = {
  mintAddress: string;
  decimals: number;
  name: string;
  symbol: string;
};

export enum OperationType {
  Supply = 'supply',
  Borrow = 'borrow',
  Repay = 'repay',
  Withdraw = 'withdraw',
}

export enum SymmetryOperationType {
  Deposit = 'deposit',
  Withdraw = 'withdraw',
  Create = 'create',
  Edit = 'edit',
}

export enum PointsProviderType {
  Kamino = 'kamino',
  Symmetry = 'symmetry',
  Drift = 'drift',
  All = 'all',
}

export enum ProviderType {
  Kamino = 'kamino',
  Marginify = 'marginify',
  Pyth = 'pyth',
}

export type TransactionDataType = {
  serializedTx: Uint8Array;
};

// Balances
export enum BalanceProviderType {
  Kamino = 'kamino',
  Symmetry = 'symmetry',
  Wallet = 'wallet',
  All = 'all',
}

export enum BalanceOperationType {
  Borrowed = 'borrow',
  Deposited = 'supply',
  WalletBalance = 'walletBalance',
  Staked = 'stake',
  All = 'all',
}

// todo: amountRaw
export type BalanceType = {
  symbol: string;
  mintAddress: string;
  amount: string;
  value: string;
  type?: string;
};
