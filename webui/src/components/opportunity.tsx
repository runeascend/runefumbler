import { CheckIcon } from "lucide-react";
import { Button } from "./ui/button";
import {
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "./ui/card";
import { Cross1Icon } from "@radix-ui/react-icons";
import { z } from "zod";
import { opportunitySchema, useActionMutation } from "@/lib/api";

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
		<Card className="grow">
			<CardHeader>
				<CardTitle>{props.opportunity.name}</CardTitle>
			</CardHeader>
			<CardContent>
				B: {props.opportunity.buy}
				<br />
				S: {props.opportunity.sell}
				<br />
				T: {props.opportunity.time}
				<br />
				TTL: {props.opportunity.ttl}
			</CardContent>
			<CardFooter className="gap-1.5">
				<Button size="sm" onClick={() => buyOpp()}>
					<CheckIcon />
				</Button>
				<Button
					size="sm"
					onClick={() => deleteOpp()}
					variant="destructive"
				>
					<Cross1Icon />
				</Button>
			</CardFooter>
		</Card>
	);
}
