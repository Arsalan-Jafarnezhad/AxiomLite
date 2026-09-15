from django.test import TestCase, RequestFactory

from weblog.models import Article, Reaction
from weblog.permissions import require_article_owner, require_comment_owner, user_can_edit_article
from weblog.selectors.tag import tag_with_articles, tags
from weblog.services.reactions import reaction_summary, toggle_reaction, user_reactions
from weblog.services.search import autocomplete, search_articles, similar_articles
from weblog.services.seo import generate_meta_description, generate_meta_title, update_seo
from weblog.tests.factories import ArticleFactory, TagFactory, UserFactory, CommentFactory
from weblog.utils.markdown import render_markdown
from weblog.utils.reading_time import reading_time, word_count
from weblog.utils.sentiment import average_polarity, is_negative, is_positive, sentiment_label
from weblog.utils.slug import unique_slug


class WeblogPermissionSelectorTests(TestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.other = UserFactory()
        self.article = ArticleFactory(author=self.owner)

    def test_article_and_comment_ownership_boundaries(self):
        self.assertTrue(user_can_edit_article(self.owner, self.article))
        self.assertFalse(user_can_edit_article(self.other, self.article))
        with self.assertRaises(Exception):
            require_article_owner(self.other, self.article)
        comment = CommentFactory(article=self.article, author=self.owner)
        with self.assertRaises(Exception):
            require_comment_owner(self.other, comment)

    def test_tag_selector_prefetches_and_returns_all_tags(self):
        tag = TagFactory()
        self.article.tags.add(tag)
        selected = tag_with_articles(tag.slug)
        self.assertIn(self.article, selected.articles.all())
        self.assertIn(tag, tags())


class WeblogServicesAndUtilsTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.article = ArticleFactory(author=self.user, title="Unique Django Search")

    def test_search_autocomplete_and_similar_articles(self):
        self.assertIn(self.article, search_articles("Django"))
        self.assertEqual(autocomplete("Unique", limit=1), [self.article.title])
        similar = ArticleFactory(category=self.article.category)
        self.assertIn(similar, similar_articles(self.article))
        self.assertFalse(search_articles("").exists())

    def test_reactions_toggle_summary_and_anonymous_set(self):
        created, reaction = toggle_reaction(article=self.article, user=self.user, emoji="👍")
        self.assertTrue(created)
        self.assertEqual(reaction.emoji, "👍")
        self.assertEqual(user_reactions(self.article, self.user), {"👍"})
        self.assertEqual(reaction_summary(self.article)[0]["count"], 1)
        removed, value = toggle_reaction(article=self.article, user=self.user, emoji="👍")
        self.assertFalse(removed)
        self.assertIsNone(value)
        with self.assertRaises(ValueError):
            toggle_reaction(article=self.article, user=self.user, emoji="invalid")

    def test_seo_markdown_reading_and_sentiment_helpers(self):
        self.assertEqual(generate_meta_title(self.article), self.article.title)
        self.assertEqual(generate_meta_description(self.article), self.article.summary)
        seo = update_seo(self.article, meta_title="SEO title")
        self.assertEqual(generate_meta_title(self.article), "SEO title")
        self.assertIn("<h1>", render_markdown("# Hello"))
        self.assertEqual(word_count("<p>one two</p>"), 2)
        self.assertEqual(reading_time("one two", wpm=1), 2)
        self.assertTrue(is_positive("This is excellent and wonderful"))
        self.assertTrue(is_negative("This is terrible and awful"))
        self.assertEqual(sentiment_label(0), "neutral")
        self.assertAlmostEqual(average_polarity(["good", "bad"]), 0.0, places=1)

    def test_unique_slug_adds_suffix(self):
        self.assertEqual(unique_slug(Article, self.article.title), f"{self.article.slug}-2")
        self.assertEqual(unique_slug(Article, self.article.slug, exclude_pk=self.article.pk), self.article.slug)
