import { useOpportunities, usePositions } from "./lib/api";
import Opportunity from "./components/opportunity";
import Position from "./components/position";
import { useEffect } from 'react';
import { toast } from 'sonner';
import styles from './app.module.css';

export default function App() {
	const { data: opportunities, error: oppErr } = useOpportunities();
	const { data: positions, error: posErr } = usePositions();

	useEffect(() => {
		if (typeof oppErr !== 'undefined') {
			console.error(oppErr);
			toast.error(JSON.stringify(oppErr));
		}
	}, [oppErr]);

	useEffect(() => {
		if (typeof posErr !== 'undefined') {
			console.error(posErr);
			toast.error(JSON.stringify(posErr));
		}
	}, [posErr]);

	return (
		<div className={styles.column}>
			<h1>runefumbler</h1>
			<span>fumbling millions of gold since 2024</span>
			<h2 className={styles.heading}>Opportunities</h2>
			<div className={styles.oppRow}>
				{typeof opportunities === 'undefined' || opportunities?.length === 0 && (
					<div className={styles.noOpps}>
						No opportunities, no gold, no bitches, nothing
					</div>
				)}
				{opportunities?.map((o, i) => (
					<Opportunity key={i} opportunity={o} index={i} />
				))}
			</div>
			<h2 className={styles.heading}>Positions</h2>
			<div className={styles.posRow}>
				{positions?.map((p, i) => (
					<Position key={i} position={p} index={i} />
				))}
			</div>
		</div>
	);
}
