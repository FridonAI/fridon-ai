import { PublicKey } from '@metaplex-foundation/js';
import { HttpException, Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { AccountLayout, TOKEN_PROGRAM_ID } from 'spl';
import { BlockchainTools } from '../utils/tools/blockchain-tools';
import { Decimal } from 'decimal.js';
import { WSOL_MINT_ADDRESS } from '../utils/constants';
import { TokenAmount } from '../utils/tools/token-amount';

export type TokenBalance = {
  mint: string;
  amount: string;
  amountRaw: number;
};

@Injectable()
export class WalletFactory {
  constructor(
    private readonly connection: Connection,
    private readonly tools: BlockchainTools,
    // private readonly blockchainService: BlockchainService,
  ) {}

  async loadTokenBalancesStalled(publicKey: string) {
    const wallet = new PublicKey(publicKey);
    const mintAddresses = await this.tools.getMintAddresses();

    // fetch sol token account
    const solAccountInfo = await this.connection.getAccountInfo(wallet);

    if (!solAccountInfo) {
      throw new HttpException('Sol account not found', 404);
    }

    const { value } = await this.connection.getTokenAccountsByOwner(wallet, {
      programId: TOKEN_PROGRAM_ID,
    });

    const balances = new Map(
      value
        .map((x) => AccountLayout.decode(x.account.data))
        .map(
          ({ amount, mint }) =>
            [mint.toBase58(), new Decimal(amount.toString(10))] as const,
        )
        .filter((x) => mintAddresses.includes(x[0])),
    );

    balances.set(
      WSOL_MINT_ADDRESS.toBase58(),
      new Decimal(solAccountInfo.lamports),
    );

    return balances;
  }

  async getWalletBalances(
    publicKey: string,
    eligibleMintAddresses: string[],
    mintAddresses: string[] = [],
  ): Promise<TokenBalance[]> {
    const resp = await this.connection.getParsedTokenAccountsByOwner(
      new PublicKey(publicKey),
      { programId: TOKEN_PROGRAM_ID },
      'confirmed',
    );

    const balances = resp.value
      .map((val) => {
        if (
          !eligibleMintAddresses.includes(val.account.data.parsed.info.mint)
        ) {
          return null;
        }
        if (
          mintAddresses.length > 0 &&
          !mintAddresses.includes(val.account.data.parsed.info.mint)
        ) {
          return null;
        }

        return {
          mint: val.account.data.parsed.info.mint,
          amount: val.account.data.parsed.info.tokenAmount.uiAmountString,
          amountRaw: parseInt(val.account.data.parsed.info.tokenAmount.amount),
        };
      })
      .filter((val) => val !== null) as TokenBalance[];

    const solBalance = await this.fetchSolBalance(new PublicKey(publicKey));
    if (
      mintAddresses.length === 0 ||
      mintAddresses.includes(WSOL_MINT_ADDRESS.toBase58())
    ) {
      return [...balances, solBalance];
    }

    return balances;
  }

  private async fetchSolBalance(publicKey: PublicKey) {
    const accountInfo = await this.connection.getAccountInfo(publicKey);

    if (!accountInfo) {
      return {
        mint: WSOL_MINT_ADDRESS.toBase58(),
        amountRaw: 0,
        amount: '0',
      };
    }

    return {
      mint: WSOL_MINT_ADDRESS.toBase58(),
      amountRaw: accountInfo!.lamports,
      amount: new TokenAmount(accountInfo!.lamports, 9, true).fixed(),
    };
  }
}
