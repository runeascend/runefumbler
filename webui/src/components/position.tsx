import {
	Card,
	CardHeader,
	CardTitle,
	CardContent,
	CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { positionSchema, useActionMutation } from "@/lib/api";
import { z } from "zod";

import styles from './position.module.css';

export interface PositionProps {
	index: number;
	position: z.infer<typeof positionSchema>;
}

export default function Position(props: PositionProps) {
	const { mutateAsync: collectPos } = useActionMutation(
		"collect",
		props.index,
	);
	const { mutateAsync: sellPos } = useActionMutation("sell", props.index);
	const { mutateAsync: exitPos } = useActionMutation("exit", props.index);

	if (props.position.state === 'pending') {
		return (
			<div className={styles.position}>
				<div className={styles.pendingText}>
					Pending...
				</div>
			</div>
		);
	}

	return (
		<div className={styles.position}>
			<div className={styles.header}>
				<CardTitle>{props.position.name}</CardTitle>
				{props.position.state !== 'pending' && props.position.name !== ''&& 
				<a className={styles.openInGrafana} target="_blank" href={`http://73.168.8.251:13300/d/b1e39934-2a88-4e7d-9336-de298905e4a5/mind-the-gap?orgId=1&refresh=5s&var-Items=${encodeURIComponent(props.position.name)}`}></a>}
			</div>
			<CardContent>
				<span>State</span>
				<span>{props.position.state}</span>
				<span>Buy price</span>
				<span className={styles.gold}>{props.position.buy_price}</span>
				<span>Sell price</span>
				<span className={styles.gold}>{props.position.sell_price}</span>
			</CardContent>
			<div className={styles.actionRow}>
				<button onClick={() => collectPos()}>
					<span>Collect</span>
				</button>
				<button onClick={() => sellPos()}>
					<span>Sell</span>
				</button>
				<button onClick={() => exitPos()}>
					<span>Exit</span>
				</button>
			</div>
		</div>
	);
}
