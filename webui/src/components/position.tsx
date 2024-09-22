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

	return (
		<Card className="grow">
			<CardHeader>
				<CardTitle>{props.position.name}</CardTitle>
			</CardHeader>
			<CardContent>
				State: {props.position.state}
				<br />
				Buy Price: {props.position.buy_price}
				<br />
				Sell Price: {props.position.sell_price}
			</CardContent>
			<CardFooter className="gap-1.5">
				<Button
					variant="secondary"
					size="sm"
					onClick={() => collectPos()}
				>
					C
				</Button>
				<Button variant="secondary" size="sm" onClick={() => sellPos()}>
					S
				</Button>
				<Button variant="secondary" size="sm" onClick={() => exitPos()}>
					E
				</Button>
			</CardFooter>
		</Card>
	);
}
