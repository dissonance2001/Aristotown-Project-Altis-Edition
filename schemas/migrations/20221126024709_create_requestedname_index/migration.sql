CREATE INDEX "Club_requestedName_fulltext_index"
    ON "Club" USING GIN (to_tsvector('english', "requestedName"));
