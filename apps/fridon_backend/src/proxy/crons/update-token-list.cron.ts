import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { JupiterTokenListAdapter } from "../adapters/token-list/token-list.adapter";
import { Cron, CronExpression } from "@nestjs/schedule";

@Injectable()
export class UpdateTokenList implements OnModuleInit {
    private readonly logger = new Logger(UpdateTokenList.name);

    constructor(
        private readonly jupiterTokenListAdapter: JupiterTokenListAdapter,
    ) {}

    async onModuleInit() {
        this.logger.log('Called Update Token List onModuleInit');

        this.jupiterTokenListAdapter.resetTokenList();
        await this.jupiterTokenListAdapter.getTokenList();
    }

    @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
    async execute() {
        this.logger.log('Called Update Token List Cron Job');

        this.jupiterTokenListAdapter.resetTokenList();
        await this.jupiterTokenListAdapter.getTokenList();
    }
}
