from typing import List

from pydantic import BaseModel, Field


class UILink(BaseModel):
    name: str = Field(..., description="Name of the link")
    url: str = Field(..., description="URL of the link")
    icon: str = Field(..., description="Icon of the link (font-awesome class or image url)")


class IconConfig(BaseModel):
    favicon: str = Field("/static/favico.png", description="Favicon URL")
    brand: str = Field("/static/img/brand.png", description="Brand logo URL")


class ViewConfig(BaseModel):
    links: List[UILink] = Field(default_factory=list, description="List of links")


class UIConfig(BaseModel):
    icons: IconConfig = Field(default_factory=IconConfig, description="Icon configuration for the UI")
    about: ViewConfig = Field(default_factory=ViewConfig, description="View configuration for the about page")
    slo: ViewConfig = Field(default_factory=ViewConfig, description="Extra View configuration for the SLO page")
    status: ViewConfig = Field(default_factory=ViewConfig, description="Extra View configuration for the Status page")
