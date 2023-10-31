export type Notification = {
	status: string;
	message: string;
}

export type User = {
	email: string | undefined;
	email_verified: boolean | undefined;
	family_name: string | undefined;
	given_name: string | undefined;
	locale: string | undefined;
	name: string;
	nickname: string | undefined;
	picture: string | undefined;
	sub: string;
	updated_at: string | undefined;
};

export type Namespace = {
	user: string;
	namespace: string;
	created_at: string;
}


export type Document = {
	user: string;
	namespace: string;
	title: string;
	content: string;
	created_at: string;
}

export type Post = {
	user: string | User;
	namespace: string;
	title: string;
	content: string;
	created_at: string;
}

export type Message = {

	role: string;
	content: string;

}

export type Uploads = {
	user: string;
	namespace: string;
	key: string;
	created_at: string;
	content_type: string;
	size: number;
	pages?: number;
}