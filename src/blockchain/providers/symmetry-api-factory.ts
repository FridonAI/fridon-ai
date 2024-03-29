import { Connection } from '@solana/web3.js';

import { Injectable } from '@nestjs/common';
import { BasketsSDK, TokenSettings } from '@symmetry-hq/baskets-sdk';
import { DONATION_ADDRESS } from '../utils/constants';

@Injectable()
export class KaminoFactory {
    constructor(private connection: Connection) { }

    async createBasket() {
        let basketsSdk: BasketsSDK = await BasketsSDK.init(
            // rpc connection
            this.connection,
        );


        // load list of supported tokens(returns TokenSettings array)
        let tokens: TokenSettings[] = basketsSdk.getTokenListData();

        console.log(tokens);

        // get tokenId(tokenId in symmetry supported tokens) from mint
        let tokenId = basketsSdk.tokenIdFromMint(
            "So11111111111111111111111111111111111111112"
        );

        console.log(tokenId);

        sdk.createBasket({
            name: basketName,
            symbol: basketSymbol,
            uri: basketDescription,
            hostPlatform: DONATION_ADDRESS,
            hostPlatformFee: 0,
            manager: wallet.publicKey,
            managerFee: depositFee * 100,
            activelyManaged: type,
            assetPool: Array.from(new Set([0, ...basketComposition.map(x => x.id)])),
            refilterInterval: basketSettings.refilterInterval,
            reweightInterval: basketSettings.reweightInterval,
            rebalanceInterval: basketSettings.rebalanceInterval,
            rebalanceThreshold: basketSettings.rebalanceThreshold,
            rebalanceSlippage: slippageTolerance * 100,
            lpOffsetThreshold: basketSettings.lpOffsetThreshold,
            disableRebalance: basketSettings.disableRebalance,
            disableLp: basketSettings.disableLP,
            rules: basketComposition.map(x => {
                return {
                    totalWeight: x.weight,
                    fixedAsset: x.id,
                    filterBy: 0, numAssets: 1,
                    filterDays: 0, sortBy: 0, weightBy: 0,
                    weightDays: 0, weightExpo: 0, excludeAssets: [],
                }
            })
        });


    }


    async createBasketApi(
        walletAddress: string,
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
        }
    ) {
        const { basketSymbol, basketName, basketUri } = basketParams;
        const hostPlatformFee = basketParams.hostPlatformFee !== undefined ? basketParams.hostPlatformFee : 10;
        const depositFee = basketParams.depositFee !== undefined ? basketParams.depositFee : 50;
        const mutable = basketParams.mutable !== undefined ? basketParams.mutable : true;
        const rebalanceInterval = basketParams.rebalanceInterval !== undefined ? basketParams.rebalanceInterval : 3600;
        const rebalanceThreshold = basketParams.rebalanceThreshold !== undefined ? basketParams.rebalanceThreshold : 300;
        const slippage = basketParams.slippage !== undefined ? basketParams.slippage : 100;
        const lpOffsetThreshold = basketParams.lpOffsetThreshold !== undefined ? basketParams.lpOffsetThreshold : 0;
        const disableRebalance = basketParams.disableRebalance !== undefined ? basketParams.disableRebalance : 0;

        const symmetryHost = "4Vry5hGDmbwGwhjgegHmoitjMHniSotpjBFkRuDYHcDG";
        const basketParameters = {
            symbol: basketSymbol, // 3-10 ['a'-'z','A'-'Z','0'-'9'] characters
            name: basketName, // 3-60 characters
            uri: basketUri, // can be left as empty and configured later.
            hostPlatform: DONATION_ADDRESS, // publicKey - string.
            hostPlatformFee: hostPlatformFee, // Fee in basis points (bps). 10 bps = 0.1%
            creator: walletAddress, // wallet publickey of creator (string) .
            depositFee: depositFee, // Fee on deposits, paid to the basket creator - 0.5% .
            type: mutable, // 1 = Mutable, Creator has authority to edit basket.
            rebalanceInterval: 3600, // Rebalance checks are done every hour.
            rebalanceThreshold: 300, // Rebalance will be triggered when asset weights deviate from their target weights by 3% .
            slippage: 100, // Maximum allowed slippage for rebalance transactions, in bps 100 = 1%.
            lpOffsetThreshold: 0, // EXPERIMENTAL: Defines liquidity pool behavior for rebalancing. 0 disables this feature.
            disableRebalance: 0, // 0 - Automatic rebalances are enabled.
            disableLp: 1, // 1 - Liquidity pool functionality is disabled.
            composition: [
                { token: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", weight: 40 }, // USDC
                { token: "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", weight: 60 }, // BONK
            ],
        };
        let request = await fetch('https://api.symmetry.fi/baskets/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(basketParameters),
        });
        let response = await request.json();

        if (response.success) {
            const {
                createTransaction,
                compositionTransaction,
                restructureTransaction
            } = response;

            // Decode the base64 encoded transactions provided by the API.
            const createTx = Transaction.from(Buffer.from(createTransaction, 'base64'));
            const compositionTx = Transaction.from(Buffer.from(compositionTransaction, 'base64'));
            const restructureTx = Transaction.from(Buffer.from(restructureTransaction, 'base64'));

            // Sign and send each transaction to the Solana blockchain.
            let signedCreate = await wallet.signTransaction(createTx);
            let createTxid = await connection.sendRawTransaction(signedCreate.serialize(), { skipPreflight: true });
            console.log('createTxid', createTxid);

            // Transactions need to be executed in the correct order, so make sure each transaction is confirmed before sending the next one.
            // Repeat the process for composition and restructure transactions.
            let signedComposition = await wallet.signTransaction(compositionTx);
            let compositionTxid = await connection.sendRawTransaction(signedComposition.serialize(), { skipPreflight: true });
            console.log('compositionTxid', compositionTxid);

            let signedRestructure = await wallet.signTransaction(restructureTx);
            let restructureTxid = await connection.sendRawTransaction(signedRestructure.serialize(), { skipPreflight: true });
            console.log('restructureTxid', restructureTxid);

            console.log('Basket created successfully');
        } else {
            console.error('Something went wrong', response);
        }

    }
}
