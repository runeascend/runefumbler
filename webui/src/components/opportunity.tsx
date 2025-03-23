import { z } from "zod";
import { opportunitySchema, useActionMutation } from "@/lib/api";
import styles from './cards.module.css';

export interface OpportunityProps {
	index: number;
	opportunity: z.infer<typeof opportunitySchema>;
}

export default function Opportunity(props: OpportunityProps) {
	const { mutateAsync: buyOpp } = useActionMutation("buy", props.index);
	const { mutateAsync: deleteOpp } = useActionMutation(
		"delete_opportunity",
		props.index,
	);

	return (
		<div className={styles.card}>
			<div className={styles.header}>
				<div>{props.opportunity.name}</div>
				<a className={styles.openInGrafana} target="_blank" href={`http://73.168.8.251:13300/d/b1e39934-2a88-4e7d-9336-de298905e4a5/mind-the-gap?orgId=1&refresh=5s&var-Items=${encodeURIComponent(props.opportunity.name)}`}>
					<div className={styles.grafanaIcon}></div>
					<div className={styles.icon}></div>
				</a>
			</div>
			<div className={styles.info}>
				<span>Buy</span>
				<span className={styles.gold}>{props.opportunity.buy}</span>
				<span>Sell</span>
				<span className={styles.gold}>{props.opportunity.sell}</span>
				<span>Time</span>
				<span className={styles.time}>{props.opportunity.time}</span>
			</div>
			<div className={styles.actionRow}>
				<button className={styles.buy} onClick={() => buyOpp()}>
					<span>
						Buy
					</span>
				</button>
				<button className={styles.delete} onClick={() => deleteOpp()}>
					<span>Delete</span>
				</button>
			</div>
		</div>
	);
}
