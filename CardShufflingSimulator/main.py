import pygame
pygame.init()

import utilities as uti
import shuffles as shuff
import button as but
import slider as sli
import marker as mar
import display

pygame.display.set_caption("Shuffling simulator")


def main():
    deck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
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

            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if not deckGenerated:
                        deck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                        deckGenerated = True
                    deck, score = shuff.Shuffle(deck, uti.settings, deckHistory)

                elif event.key == pygame.K_r:
                    deck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                    deckGenerated = True

                elif event.key == pygame.K_q:
                    running = False
            
            # Button presses
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in but.buttons.values():
                        if button.button.collidepoint(event.pos):
                            
                            # Shuffle the deck button
                            if button.name == "shuffle":
                                if button.value == False:
                                    deck, score = shuff.Shuffle(deck, uti.settings, deckHistory)
                                    button.value = True
                            
                            # Reset the deck button
                            elif button.name == "reset":
                                if button.value == False:
                                    deck, deckHistory, score = uti.InitializeDeck(uti.settings["deckSize"])
                                    deckGenerated = True
                                    button.value = True
                                    #uti.ExpectedIdealSimulator(52, 10000)
                            
                            # Change shuffles button        
                            elif button.name == "assign shuffle":
                                button.nextValue()
                                uti.settings["shuffle"] = button.value
                                print("Selected shuffle: " + str(button.value))
                            
                            # Change display type of the deck button
                            elif button.name == "change view":
                                button.nextValue()
                                uti.settings["displayType"] = button.value
                                print("Selected view: " + str(button.value))
                            
                            # Queue a shuffle button
                            elif button.name == "queue":
                                if button.value == False:
                                    uti.QueueShuffle()
                                    button.value = True
                            
                            # Remove a shuffle from the queue button        
                            elif button.name == "remove":
                                if button.value == False:
                                    uti.RemoveShuffle()
                                    button.value = True
            
            # Change buttons value back to false if mouse button is lifted                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if but.buttons["shuffle"].value == True:
                        but.buttons["shuffle"].value = False
                        but.buttons["shuffle"].valueIndex = 1
                    elif but.buttons["reset"].value == True:
                        but.buttons["reset"].value = False
                        but.buttons["reset"].valueIndex = 1
                    elif but.buttons["queue"].value == True:
                        but.buttons["queue"].value = False
                        but.buttons["queue"].valueIndex = 1
                    elif but.buttons["remove"].value == True:
                        but.buttons["remove"].value = False
                        but.buttons["remove"].valueIndex = 1
                        
        # Slider logic
        if mouse_held[0]:
            for slider in sli.sliders.values():
                if slider.slider.collidepoint(mouse_x, mouse_y):
                    slider.handle.x = max(slider.minX, min(slider.maxX, mouse_x - slider.handle.width // 2))
                    slider.value = (slider.handle.x - slider.minX) / (slider.maxX - slider.minX)
                    uti.settings[slider.name] = slider.value
                    
        # Button drawing
        for button in but.buttons.values():
            if button.name == "shuffle" or button.name == "reset":
                if button.value == False:
                    button.draw(uti.SCREEN, uti.GREY, 10, 10, 0, 0)
                else:
                    button.draw(uti.SCREEN, uti.DARK_GREY, 10, 15, 0, 0)
            elif button.name == "queue" or button.name == "remove":
                if button.value == False:
                    button.draw(uti.SCREEN, uti.GREY, 4, 4, 0, 0)
                else:
                    button.draw(uti.SCREEN, uti.DARK_GREY, 5, 5, 0, 0)
            else:
                button.draw(uti.SCREEN, uti.GREY, 0, -25, 5, 0)
        
        # Slider drawing
        for slider in sli.sliders.values():
            slider.draw(uti.SCREEN, uti.GREY, uti.DARK_GREY)
        
        # Queue marker drawing        
        if mar.markers:
            for marker in mar.markers:
                marker.Draw(uti.SCREEN, marker.color, marker.name)
        
        
        # Score drawing        
        uti.Draw_text(str(int(score.absoluteDistanceScore * 100)) + "% :Absolut distance score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 10)
        uti.Draw_text(str(int(score.relativeDistanceScore * 100)) + "% :Relative distance score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 30)
        uti.Draw_text(str(int(score.orderScore * 100)) + "% :Order score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 50)
        uti.Draw_text(str(int(score.consecutiveTrendScore * 100)) + "% :Consecutive trend score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 70)
        uti.Draw_text(str(int(score.linearPatternScore * 100)) + "% :Linear pattern score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 90)
        
        uti.Draw_text(str(int(score.edgePreservationScore * 100)) + "% :Edge preservation score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 130)
        
        uti.Draw_text(str(int(score.repeatingRankScore * 100)) + "% :Repeating rank score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 170)
        uti.Draw_text(str(int(score.trendingRankScore * 100)) + "% :Trending rank score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 190)
        uti.Draw_text(str(int(score.repeatingSuitScore * 100)) + "% :Repeating suit score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 210)
        uti.Draw_text(str(int(score.suitPatternScore * 100)) + "% :Suit pattern score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 230)
        uti.Draw_text(str(int(score.repeatingColorScore * 100)) + "% :Repeating color score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 250)
        
        uti.Draw_text(str(int(score.totalScore * 100)) + "% :Total score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 310)
        uti.Draw_text(str(int(score.humanScore * 100)) + "% :Human score", uti.FONT, uti.BLACK, uti.settingsTabX + 10, uti.settingsTabY + 330)
        
        # Deck drawing
        display.DisplayDeckHistory(deckHistory, uti.settings["displayType"])
        
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()