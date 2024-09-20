import { Connection, Transaction, VersionedTransaction } from '@solana/web3.js';

import { HttpException, Injectable } from '@nestjs/common';
import { DONATION_ADDRESS } from '../utils/constants';
import { TransactionFactory } from '../factories/transaction-factory';
import { PublicKey } from '@metaplex-foundation/js';
import { BlockchainTools } from '../utils/tools/blockchain-tools';
import { TokenBalance } from './wallet-factory';
import { TOKEN_PROGRAM_ID } from 'spl';
import { BalanceType } from '../utils/types';

export const SYMMETRY_CREATE_BASKET_API =
  'https://api.symmetry.fi/baskets/create';
export const SYMMETRY_EDIT_BASKET_API = 'https://api.symmetry.fi/baskets/edit';
export const SYMMETRY_DEPOSIT_BASKET_API =
  'https://api.symmetry.fi/baskets/deposit';

export type TokenCompositionType = {
  token: string;
  weight: number;
};

//// example
// [
//     { token: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", weight: 40 }, // USDC
//     { token: "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", weight: 60 }, // BONK
// ]
@Injectable()
export class SymmetryApiFactory {
  constructor(
    private readonly transactionFactory: TransactionFactory,
    private readonly tools: BlockchainTools,
    private readonly connection: Connection,
  ) {}

  async createBasketApi(
    walletAddress: string,
    composition: TokenCompositionType[],
    basketParams: {
      basketSymbol: string;
      basketName: string;
      basketUri: string;
      mutable?: boolean;
      hostPlatformFee?: number;
      depositFee?: number;
      rebalanceInterval?: number;
      rebalanceThreshold?: number;
      slippage?: number;
      lpOffsetThreshold?: number;
      disableRebalance?: number;
      disableLp?: number;
    },
  ): Promise<VersionedTransaction[]> {
    const feePayer = new PublicKey(walletAddress);
    const { basketSymbol, basketName, basketUri } = basketParams;
    const hostPlatformFee =
      basketParams.hostPlatformFee !== undefined
        ? basketParams.hostPlatformFee
        : 10;
    const depositFee =
      basketParams.depositFee !== undefined ? basketParams.depositFee : 50;
    const mutable =
      basketParams.mutable !== undefined ? basketParams.mutable : true;
    const rebalanceInterval =
      basketParams.rebalanceInterval !== undefined
        ? basketParams.rebalanceInterval
        : 3600;
    const rebalanceThreshold =
      basketParams.rebalanceThreshold !== undefined
        ? basketParams.rebalanceThreshold
        : 300;
    const slippage =
      basketParams.slippage !== undefined ? basketParams.slippage : 100;
    const lpOffsetThreshold =
      basketParams.lpOffsetThreshold !== undefined
        ? basketParams.lpOffsetThreshold
        : 0;
    const disableRebalance =
      basketParams.disableRebalance !== undefined
        ? basketParams.disableRebalance
        : 0;
    const disableLp =
      basketParams.disableLp !== undefined ? basketParams.disableLp : 1;

    const basketParameters = {
      symbol: basketSymbol, // 3-10 ['a'-'z','A'-'Z','0'-'9'] characters
      name: basketName, // 3-60 characters
      uri: basketUri, // can be left as empty and configured later.
      hostPlatform: DONATION_ADDRESS, // publicKey - string.
      hostPlatformFee: hostPlatformFee, // Fee in basis points (bps). 10 bps = 0.1%
      creator: walletAddress, // wallet publickey of creator (string) .
      depositFee: depositFee, // Fee on deposits, paid to the basket creator - 0.5% .
      type: mutable, // 1 = Mutable, Creator has authority to edit basket.
      rebalanceInterval: rebalanceInterval, // Rebalance checks are done every hour.
      rebalanceThreshold: rebalanceThreshold, // Rebalance will be triggered when asset weights deviate from their target weights by 3% .
      slippage: slippage, // Maximum allowed slippage for rebalance transactions, in bps 100 = 1%.
      lpOffsetThreshold: lpOffsetThreshold, // EXPERIMENTAL: Defines liquidity pool behavior for rebalancing. 0 disables this feature.
      disableRebalance: disableRebalance, // 0 - Automatic rebalances are enabled.
      disableLp: disableLp, // 1 - Liquidity pool functionality is disabled.
      composition: composition,
    };

    const request = await fetch(SYMMETRY_CREATE_BASKET_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(basketParameters),
    });
    const response = await request.json();

    console.log('response', response);

    if (response.success) {
      const {
        createTransaction,
        compositionTransaction,
        restructureTransaction,
      } = response;

      // Decode the base64 encoded transactions provided by the API.
      const createTx = Transaction.from(
        Buffer.from(createTransaction, 'base64'),
      );
      const compositionTx = Transaction.from(
        Buffer.from(compositionTransaction, 'base64'),
      );
      const restructureTx = Transaction.from(
        Buffer.from(restructureTransaction, 'base64'),
      );

      const versionTransactionsPromise = [
        this.transactionFactory.generateTransactionV0(
          createTx.instructions,
          feePayer,
        ),
        this.transactionFactory.generateTransactionV0(
          compositionTx.instructions,
          feePayer,
        ),
        this.transactionFactory.generateTransactionV0(
          restructureTx.instructions,
          feePayer,
        ),
      ];

      return await Promise.all(versionTransactionsPromise);
    } else {
      console.error('Something went wrong', response);
      throw new HttpException(
        'Something went wrong while creating the basket.',
        403,
      );
    }
  }

  // todo: we have to talk how to use this API.
  async editBasketApi(
    walletAddress: string,
    creator: string,
    basketMintAddress: string,
    composition: TokenCompositionType[],
    basketParams: {
      basketSymbol: string;
      basketName: string;
      basketUri: string;
      mutable: boolean;
      hostPlatformFee: number;
      depositFee: number;
      rebalanceInterval: number;
      rebalanceThreshold: number;
      slippage: number;
      lpOffsetThreshold: number;
      disableRebalance: number;
      disableLp: number;
    },
  ): Promise<VersionedTransaction> {
    const payer = new PublicKey(walletAddress);
    const {
      depositFee,
      rebalanceInterval,
      rebalanceThreshold,
      slippage,
      lpOffsetThreshold,
      disableRebalance,
      disableLp,
    } = basketParams;
    const editParameters = {
      creator: creator,
      basket: basketMintAddress,
      depositFee,
      rebalanceInterval,
      rebalanceThreshold,
      slippage,
      lpOffsetThreshold,
      disableRebalance,
      disableLp,
      composition,
    };
    const request = await fetch(SYMMETRY_EDIT_BASKET_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editParameters),
    });
    const response = await request.json();

    if (response.success) {
      const { editTransaction } = response;

      const editTx = Transaction.from(Buffer.from(editTransaction, 'base64'));

      return await this.transactionFactory.generateTransactionV0(
        editTx.instructions,
        payer,
      );
    } else {
      console.error('Something went wrong', response);
      throw new HttpException(
        'Something went wrong while editing the basket.',
        403,
      );
    }
  }

  async depositBasketApi(
    walletAddress: string,
    basketName: string,
    amount: number,
  ): Promise<VersionedTransaction> {
    const payer = new PublicKey(walletAddress);
    basketName;
    const basketMintAddress = '4RofqKG4d6jfUD2HjtWb2F9UkLJvJ7P3kFmyuhX7H88d';

    const depositParameters = {
      user: walletAddress,
      basket: basketMintAddress,
      amount,
    };

    const request = await fetch(SYMMETRY_DEPOSIT_BASKET_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(depositParameters),
    });
    const response = await request.json();

    if (response.success) {
      const { transaction } = response;

      // Decode the base64 encoded transactions provided by the API.
      const depositTx = Transaction.from(Buffer.from(transaction, 'base64'));

      return await this.transactionFactory.generateTransactionV0(
        depositTx.instructions,
        payer,
      );
    } else {
      console.error('Something went wrong', response);
      throw new HttpException(
        'Something went wrong while depositing the basket.',
        403,
      );
    }
  }

  async depositSingleAssetApi(
    walletAddress: string,
    basketMintAddress: string,
    tokenMintAddress: string,
    amount: number,
  ) {
    const depositParameters = {
      user: walletAddress, // string
      basket: basketMintAddress, // ySOL Basket
      tokenMint: tokenMintAddress, // mSOL
      amount: amount, // 0.5 mSOL
    };
    const request = await fetch('https://api.symmetry.fi/baskets/mint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(depositParameters),
    });
    const response = await request.json();

    if (response.success) {
      const { transaction } = response;

      // Decode the base64 encoded transactions provided by the API.
      const depositTx = Transaction.from(Buffer.from(transaction, 'base64'));

      return await this.transactionFactory.generateTransactionV0(
        depositTx.instructions,
        new PublicKey(walletAddress),
      );
    } else {
      console.error('Something went wrong', response);
      throw new HttpException(
        'Something went wrong while depositing the basket.',
        403,
      );
    }
  }

  async redeemSingleAssetApi(
    walletAddress: string,
    basketMintAddress: string,
    tokenMintAddress: string,
    amount: number,
  ) {
    const withdrawParameters = {
      user: walletAddress, // string
      basket: basketMintAddress, // ySOL Basket
      tokenMint: tokenMintAddress, // mSOL
      amount: amount, // sell 0.1 ySOL
    };
    const request = await fetch('https://api.symmetry.fi/baskets/burn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(withdrawParameters),
    });
    const response = await request.json();

    if (response.success) {
      const { transaction } = response;

      // Decode the base64 encoded transactions provided by the API.
      const withdrawTx = Transaction.from(Buffer.from(transaction, 'base64'));

      return await this.transactionFactory.generateTransactionV0(
        withdrawTx.instructions,
        new PublicKey(walletAddress),
      );
    } else {
      console.error('Something went wrong', response);
      throw new HttpException(
        'Something went wrong while redeeming the basket.',
        403,
      );
    }
  }

  // Getters
  async getWalletBaskets(
    walletAddress: string,
    rpcEndpoint: string,
    mintAddress: string | undefined,
  ) {
    rpcEndpoint;
    const walletBalances = await this.getWalletBalances(walletAddress);

    // todo: move this do cron job.
    const request = await fetch('https://api.symmetry.fi/v1/funds-getter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request: 'get_funds',
        params: {
          filters: {
            by: 'tvl',
            order: 'desc',
          },
          attributes: [
            'name',
            'symbol',
            'tvl',
            'price',
            'sortkey',
            'fund_token',
          ],
          count: 500,
          page: 1,
          actively_managed: null,
          min_tvl: 0,
        },
      }),
    });

    const response = await request.json();
    const data: {
      price: number;
      symbol: string;
      fund_token: string;
    }[] = response.result;

    const balances: BalanceType[] = walletBalances
      .map((balance) => {
        const basket = data.find(
          (basket) => basket.fund_token === balance.mint,
        );

        if (basket) {
          return {
            symbol: basket.symbol,
            mintAddress: balance.mint,
            amount: balance.amount,
            value: (parseFloat(balance.amount) * basket.price).toFixed(2),
          };
        }

        return undefined;
      })
      .filter((val) => val !== undefined) as BalanceType[];

    if (mintAddress) {
      return balances.filter((balance) => balance.mintAddress === mintAddress);
    }
    return balances;
  }

  async getAllBaskets(): Promise<SymmetryFundsType[]> {
    const request = await fetch('https://api.symmetry.fi/v1/funds-getter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request: 'get_funds',
        params: {
          filters: {
            by: 'tvl',
            order: 'desc',
          },
          attributes: [
            'current_comp_token',
            'name',
            'symbol',
            'tvl',
            'price',
            'sortkey',
            'fund_token',
          ],
          count: 25,
          page: 1,
          actively_managed: null,
          min_tvl: 0,
        },
      }),
    });
    const response = await request.json();
    const data: SymmetryFundsType[] = response.result;

    const result: any = [];

    for (const basket of data) {
      const symbols = await this.tools.convertMintAddressesToSymbols(
        basket.current_comp_token,
      );
      result.push({
        ...basket,
        current_comp_token_symbol: symbols,
      });
    }

    return result;
  }

  private async getWalletBalances(publicKey: string): Promise<TokenBalance[]> {
    const resp = await this.connection.getParsedTokenAccountsByOwner(
      new PublicKey(publicKey),
      { programId: TOKEN_PROGRAM_ID },
      'confirmed',
    );

    const balances = resp.value
      .map((val) => {
        return {
          mint: val.account.data.parsed.info.mint,
          amount: val.account.data.parsed.info.tokenAmount.uiAmountString,
          amountRaw: parseInt(val.account.data.parsed.info.tokenAmount.amount),
        };
      })
      .filter((val) => val !== null) as TokenBalance[];

    return balances;
  }
}

export type SymmetryFundsType = {
  actively_managed: boolean;
  creation_time: number;
  current_comp_token: string[];
  current_comp_token_symbol: string[];
  fund_token: string;
  manager: string;
  name: string;
  precise_historical: {
    data: Record<
      string,
      {
        price: number;
        time: number;
        tot_fee: number;
        tot_vol: number;
        tvl: number;
      }
    >;
  };
  price: number;
  sortkey: string;
  symbol: string;
  tvl: number;
};
