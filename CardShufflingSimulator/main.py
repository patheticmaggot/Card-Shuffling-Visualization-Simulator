import pygame
pygame.init()

import utilities as uti
import shuffles as shuff
import button as but
import slider as sli
import display

pygame.display.set_caption("Shuffling simulator")


def main():
    deck, startDeck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
    deckGenerated = True

    running = True
    while running:

        uti.clock.tick(60)
        uti.SCREEN.fill(uti.BACKGROUND_COLOR)
        pygame.draw.rect(uti.SCREEN, uti.SETTINGSTAB_COLOR, uti.settingsTab)
        
        mouse_held = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if not deckGenerated:
                        deck, startDeck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                        deckGenerated = True
                    deck, score = shuff.Shuffle(deck, uti.settings, deckHistory)

                elif event.key == pygame.K_r:
                    deck, startDeck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                    deckGenerated = True

                elif event.key == pygame.K_q:
                    running = False
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in but.buttons.values():
                        if button.button.collidepoint(event.pos):
                            
                            if button.name == "shuffle":
                                if button.value == False:
                                    deck, score = shuff.Shuffle(deck, uti.settings, deckHistory)
                                    button.value = True
                            elif button.name == "reset":
                                if button.value == False:
                                    deck, startDeck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                                    deckGenerated = True
                                    button.value = True
                                    #uti.ExpectedIdealSimulator(52, 10000)
                            elif button.name == "assign shuffle":
                                button.nextValue()
                                uti.settings["shuffle"] = button.value
                                print("Selected shuffle: " + str(button.value))
                            elif button.name == "change view":
                                button.nextValue()
                                uti.settings["displayType"] = button.value
                                print("Selected view: " + str(button.value))
                                
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if but.buttons["shuffle"].value == True:
                        but.buttons["shuffle"].value = False
                        but.buttons["shuffle"].valueIndex = 1
                    elif but.buttons["reset"].value == True:
                        but.buttons["reset"].value = False
                        but.buttons["reset"].valueIndex = 1
        
        if mouse_held[0]:
            for slider in sli.sliders.values():
                if slider.slider.collidepoint(mouse_x, mouse_y):
                    slider.handle.x = max(slider.minX, min(slider.maxX, mouse_x - slider.handle.width // 2))
                    slider.value = (slider.handle.x - slider.minX) / (slider.maxX - slider.minX)
                    uti.settings[slider.name] = slider.value

        for slider in sli.sliders.values():
            slider.draw(uti.SCREEN, uti.GREY, uti.DARK_GREY)
        
        for button in but.buttons.values():
            if button.name == "shuffle":
                if button.value == False:
                    button.draw(uti.SCREEN, uti.GREY, 10, 10, 0, 0)
                else:
                    button.draw(uti.SCREEN, uti.DARK_GREY, 10, 15, 0, 0)
            elif button.name == "reset":
                if button.value == False:
                    button.draw(uti.SCREEN, uti.GREY, 10, 10, 0, 0)
                else:
                    button.draw(uti.SCREEN, uti.DARK_GREY, 10, 15, 0, 0)
            else:
                button.draw(uti.SCREEN, uti.GREY, 0, -25, 5, 0)
                
        uti.Draw_text(str(int(score.absoluteDistanceScore * 100)) + "% :Absolut distance score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 10)
        uti.Draw_text(str(int(score.relativeDistanceScore * 100)) + "% :Relative distance score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 30)
        uti.Draw_text(str(int(score.orderScore * 100)) + "% :Order score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 50)
        uti.Draw_text(str(int(score.consecutiveTrendScore * 100)) + "% :Consecutive trend score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 70)
        uti.Draw_text(str(int(score.linearPatternScore * 100)) + "% :Linear pattern score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 90)
        
        uti.Draw_text(str(int(score.repeatingRankScore * 100)) + "% :Repeating rank score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 130)
        uti.Draw_text(str(int(score.trendingRankScore * 100)) + "% :Trending rank score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 150)
        
        uti.Draw_text(str(int(score.repeatingSuitScore * 100)) + "% :Repeating suit score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 190)
        uti.Draw_text(str(int(score.suitPatternScore * 100)) + "% :Suit pattern score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 210)
        
        uti.Draw_text(str(int(score.repeatingColorScore * 100)) + "% :Repeating color score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 250)
        #uti.Draw_text(str(int(score.colorPatternScore * 100)) + "% :Color pattern score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 270)
        
        uti.Draw_text(str(int(score.totalScore * 100)) + "% :Total score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 310)
        uti.Draw_text(str(int(score.humanScore * 100)) + "% :Human score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 330)
        
        
        display.DisplayDeckHistory(deckHistory, uti.settings["displayType"])
        
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()