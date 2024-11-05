"""
External API integrations for book data enrichment
"""
import requests
import httpx
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class GoogleBooksAPI:
    """
    Integration with Google Books API for book data enrichment
    FREE API - No credit card required
    Get your API key: https://console.cloud.google.com/apis/credentials
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
        self.base_url = settings.GOOGLE_BOOKS_API_URL
    
    def search_books(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for books by title, author, or ISBN
        
        Args:
            query: Search query (title, author, or ISBN)
            max_results: Maximum number of results to return
        
        Returns:
            List of book data dictionaries
        """
        cache_key = f"google_books:search:{query}:{max_results}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            params = {
                "q": query,
                "maxResults": max_results,
            }
            if self.api_key:
                params["key"] = self.api_key
            
            response = requests.get(
                f"{self.base_url}/volumes",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            books = self._parse_books(data.get("items", []))
            
            # Cache for 24 hours
            cache.set(cache_key, books, 86400)
            return books
            
        except Exception as e:
            logger.error(f"Google Books API error: {str(e)}")
            return []
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Get book details by ISBN
        
        Args:
            isbn: ISBN-10 or ISBN-13
        
        Returns:
            Book data dictionary or None
        """
        cache_key = f"google_books:isbn:{isbn}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            params = {"q": f"isbn:{isbn}"}
            if self.api_key:
                params["key"] = self.api_key
            
            response = requests.get(
                f"{self.base_url}/volumes",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            if items:
                book = self._parse_book(items[0])
                # Cache for 7 days (ISBN data doesn't change)
                cache.set(cache_key, book, 604800)
                return book
            
            return None
            
        except Exception as e:
            logger.error(f"Google Books API error for ISBN {isbn}: {str(e)}")
            return None
    
    def _parse_books(self, items: List[Dict]) -> List[Dict]:
        """Parse multiple books from API response"""
        return [self._parse_book(item) for item in items]
    
    def _parse_book(self, item: Dict) -> Dict:
        """Parse single book from API response"""
        volume_info = item.get("volumeInfo", {})
        
        return {
            "google_id": item.get("id"),
            "title": volume_info.get("title", ""),
            "authors": volume_info.get("authors", []),
            "description": volume_info.get("description", ""),
            "publisher": volume_info.get("publisher", ""),
            "published_date": volume_info.get("publishedDate", ""),
            "isbn_10": self._extract_isbn(volume_info, "ISBN_10"),
            "isbn_13": self._extract_isbn(volume_info, "ISBN_13"),
            "page_count": volume_info.get("pageCount"),
            "categories": volume_info.get("categories", []),
            "language": volume_info.get("language", "en"),
            "cover_image": self._get_cover_image(volume_info),
            "preview_link": volume_info.get("previewLink", ""),
            "info_link": volume_info.get("infoLink", ""),
            "average_rating": volume_info.get("averageRating"),
            "ratings_count": volume_info.get("ratingsCount"),
        }
    
    def _extract_isbn(self, volume_info: Dict, isbn_type: str) -> Optional[str]:
        """Extract ISBN from identifiers"""
        identifiers = volume_info.get("industryIdentifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == isbn_type:
                return identifier.get("identifier")
        return None
    
    def _get_cover_image(self, volume_info: Dict) -> Optional[str]:
        """Get best quality cover image URL"""
        image_links = volume_info.get("imageLinks", {})
        # Try to get highest quality image
        for key in ["extraLarge", "large", "medium", "small", "thumbnail", "smallThumbnail"]:
            if key in image_links:
                return image_links[key].replace("http://", "https://")
        return None


class OpenLibraryAPI:
    """
    Integration with Open Library API - 100% FREE, no API key needed!
    Documentation: https://openlibrary.org/developers/api
    """
    
    def __init__(self):
        self.base_url = settings.OPENLIBRARY_API_URL
    
    async def search_books_async(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Async search for books (for use in async views)
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of book dictionaries
        """
        cache_key = f"openlibrary:search:{query}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search.json",
                    params={"q": query, "limit": limit},
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                books = self._parse_search_results(data.get("docs", []))
                
                # Cache for 12 hours
                cache.set(cache_key, books, 43200)
                return books
                
        except Exception as e:
            logger.error(f"OpenLibrary API error: {str(e)}")
            return []
    
    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Synchronous search for books
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of book dictionaries
        """
        cache_key = f"openlibrary:search:{query}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{self.base_url}/search.json",
                params={"q": query, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            books = self._parse_search_results(data.get("docs", []))
            
            # Cache for 12 hours
            cache.set(cache_key, books, 43200)
            return books
            
        except Exception as e:
            logger.error(f"OpenLibrary API error: {str(e)}")
            return []
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Get book by ISBN
        
        Args:
            isbn: ISBN-10 or ISBN-13
        
        Returns:
            Book dictionary or None
        """
        cache_key = f"openlibrary:isbn:{isbn}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{self.base_url}/isbn/{isbn}.json",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            book = self._parse_book_details(data)
            
            # Cache for 7 days
            cache.set(cache_key, book, 604800)
            return book
            
        except Exception as e:
            logger.error(f"OpenLibrary API error for ISBN {isbn}: {str(e)}")
            return None
    
    def get_author_details(self, author_key: str) -> Optional[Dict]:
        """
        Get author details by Open Library author key
        
        Args:
            author_key: Author key (e.g., "/authors/OL23919A")
        
        Returns:
            Author dictionary or None
        """
        cache_key = f"openlibrary:author:{author_key}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{self.base_url}{author_key}.json",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            author = {
                "key": data.get("key"),
                "name": data.get("name"),
                "bio": data.get("bio", {}).get("value") if isinstance(data.get("bio"), dict) else data.get("bio"),
                "birth_date": data.get("birth_date"),
                "death_date": data.get("death_date"),
                "alternate_names": data.get("alternate_names", []),
                "photo_url": self._get_author_photo(data),
            }
            
            # Cache for 30 days
            cache.set(cache_key, author, 2592000)
            return author
            
        except Exception as e:
            logger.error(f"OpenLibrary API error for author {author_key}: {str(e)}")
            return None
    
    def _parse_search_results(self, docs: List[Dict]) -> List[Dict]:
        """Parse search results"""
        books = []
        for doc in docs:
            books.append({
                "key": doc.get("key"),
                "title": doc.get("title"),
                "authors": doc.get("author_name", []),
                "first_publish_year": doc.get("first_publish_year"),
                "isbn": doc.get("isbn", []),
                "publisher": doc.get("publisher", []),
                "cover_id": doc.get("cover_i"),
                "cover_url": self._get_cover_url(doc.get("cover_i")),
                "subject": doc.get("subject", [])[:5],  # First 5 subjects
                "language": doc.get("language", []),
                "page_count": doc.get("number_of_pages_median"),
            })
        return books
    
    def _parse_book_details(self, data: Dict) -> Dict:
        """Parse detailed book data"""
        return {
            "key": data.get("key"),
            "title": data.get("title"),
            "authors": [author.get("key") for author in data.get("authors", [])],
            "publish_date": data.get("publish_date"),
            "publishers": data.get("publishers", []),
            "isbn_10": data.get("isbn_10", []),
            "isbn_13": data.get("isbn_13", []),
            "number_of_pages": data.get("number_of_pages"),
            "subjects": data.get("subjects", []),
            "description": data.get("description", {}).get("value") if isinstance(data.get("description"), dict) else data.get("description"),
            "cover_id": data.get("covers", [None])[0],
            "cover_url": self._get_cover_url(data.get("covers", [None])[0]),
        }
    
    def _get_cover_url(self, cover_id: Optional[int], size: str = "L") -> Optional[str]:
        """Get cover image URL from cover ID"""
        if cover_id:
            return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"
        return None
    
    def _get_author_photo(self, author_data: Dict, size: str = "M") -> Optional[str]:
        """Get author photo URL"""
        photos = author_data.get("photos")
        if photos and len(photos) > 0:
            return f"https://covers.openlibrary.org/a/id/{photos[0]}-{size}.jpg"
        return None


# Initialize API clients
google_books_api = GoogleBooksAPI()
openlibrary_api = OpenLibraryAPI()

